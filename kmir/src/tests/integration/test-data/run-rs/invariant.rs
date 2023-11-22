		//Inspired by this issue: https://github.com/galacticcouncil/HydraDX-node/issues/448
        // Where the invariant: the total hub asset liquidity should be equal to the total of the hub asset in each subpool
        
        /// Remove liquidity of asset `asset` in quantity `amount` from Omnipool
		///
		/// `remove_liquidity` removes specified shares amount from given PositionId (NFT instance).
		///
		/// Asset's tradable state must contain REMOVE_LIQUIDITY flag, otherwise `NotAllowed` error is returned.
		///
		/// if all shares from given position are removed, NFT is burned.
		///
		/// Parameters:
		/// - `position_id`: The identifier of position which liquidity is removed from.
		/// - `amount`: Amount of shares removed from omnipool
		///
		/// Emits `LiquidityRemoved` event when successful.
		///
		#[pallet::weight(<T as Config>::WeightInfo::remove_liquidity())]
		#[transactional]
		pub fn remove_liquidity(
			origin: OriginFor<T>,
			position_id: T::PositionInstanceId,
			amount: Balance,
		) -> DispatchResult {
			//
			// Preconditions
			//
			let who = ensure_signed(origin)?;
			ensure!(
				T::NFTHandler::owner(&T::NFTClassId::get(), &position_id) == Some(who.clone()),
				Error::<T>::Forbidden
			);
			let position = Positions::<T>::get(position_id).ok_or(Error::<T>::PositionNotFound)?;
			ensure!(position.shares >= amount, Error::<T>::InsufficientShares);
			let stable_asset = Self::stable_asset()?;
			let asset_id = position.asset_id;
			let asset_state = Self::load_asset_state(asset_id)?;
			ensure!(
				asset_state.tradable.contains(Tradability::REMOVE_LIQUIDITY),
				Error::<T>::NotAllowed
			);
			//
			// calculate state changes of remove liquidity
			//
			let state_changes = hydra_dx_math::omnipool::calculate_remove_liquidity_state_changes(
				&(&asset_state).into(),
				amount,
				&(&position).into(),
				stable_asset,
				asset_id == T::StableCoinAssetId::get(),
			)
			.ok_or(ArithmeticError::Overflow)?;
			let new_asset_state = asset_state
				.delta_update(&state_changes.asset)
				.ok_or(ArithmeticError::Overflow)?;
			// Update position state
			let updated_position = position
				.delta_update(
					&state_changes.delta_position_reserve,
					&state_changes.delta_position_shares,
				)
				.ok_or(ArithmeticError::Overflow)?;
			//
			// Post - update states
			//
			T::Currency::transfer(
				asset_id,
				&Self::protocol_account(),
				&who,
				*state_changes.asset.delta_reserve,
			)?;
			let delta_imbalance = Self::recalculate_imbalance(&new_asset_state, state_changes.delta_imbalance)
				.ok_or(ArithmeticError::Overflow)?;
			Self::update_imbalance(delta_imbalance)?;

			Self::update_tvl(&state_changes.asset.delta_tvl)?;

			Self::update_hub_asset_liquidity(&state_changes.asset.delta_hub_reserve)?;
			// burn only difference between delta hub and lp hub amount.
			Self::update_hub_asset_liquidity(
				&state_changes
					.asset
					.delta_hub_reserve
					.merge(BalanceUpdate::Increase(state_changes.lp_hub_amount))
					.ok_or(ArithmeticError::Overflow)?,
			)?;

			// LP receives some hub asset
			if state_changes.lp_hub_amount > Balance::zero() {
				T::Currency::transfer(
					T::HubAssetId::get(),
					&Self::protocol_account(),
					&who,
					state_changes.lp_hub_amount,
				)?;
			}
			if updated_position.shares == Balance::zero() {
				// All liquidity removed, remove position and burn NFT instance
				<Positions<T>>::remove(position_id);
				T::NFTHandler::burn_from(&T::NFTClassId::get(), &position_id)?;
				Self::deposit_event(Event::PositionDestroyed {
					position_id,
					owner: who.clone(),
				});
			} else {
				Self::deposit_event(Event::PositionUpdated {
					position_id,
					owner: who.clone(),
					asset: asset_id,
					amount: updated_position.amount,
					shares: updated_position.shares,
					price: FixedU128::from_inner(updated_position.price),
				});
				<Positions<T>>::insert(position_id, updated_position);
			}
			Self::set_asset_state(asset_id, new_asset_state);
			Self::deposit_event(Event::LiquidityRemoved {
				who,
				position_id,
				asset_id,
				shares_removed: amount,
			});
			Ok(())
		}