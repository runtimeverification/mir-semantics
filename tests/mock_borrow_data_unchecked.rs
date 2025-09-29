use std::ptr;

/// Simplified Account struct, simulating the original Account structure
#[repr(C)]
pub struct Account {
    pub data_len: u64,
    // Other fields omitted, only data_len is kept
}

/// Simplified MockAccountInfo, maintaining original complexity
pub struct MockAccountInfo {
    raw: *mut Account,
    data: Vec<u8>, // Where actual data is stored
}

impl MockAccountInfo {
    /// Create a new MockAccountInfo
    pub fn new(data: Vec<u8>) -> Self {
        let mut account = Account {
            data_len: data.len() as u64,
        };
        
        Self {
            raw: &mut account as *mut Account,
            data,
        }
    }

    /// Get data pointer, simulating the original data_ptr method
    pub unsafe fn data_ptr(&self) -> *mut u8 {
        unsafe { 
            (self.raw as *const _ as *mut u8).add(std::mem::size_of::<Account>()) 
        }
    }

    /// Get data length, simulating the original data_len method
    pub unsafe fn data_len(&self) -> usize {
        unsafe { (*self.raw).data_len as usize }
    }

    /// Maintain original complexity for borrow_data_unchecked
    /// 
    /// # Safety
    ///
    /// This method is unsafe because it does not return a `Ref`, thus leaving the borrow
    /// flag untouched. Useful when an instruction has verified non-duplicate accounts.
    #[inline(always)]
    pub unsafe fn borrow_data_unchecked(&self) -> &[u8] {
        core::slice::from_raw_parts(self.data_ptr(), self.data_len())
    }
}

fn main() {
    // Create test data
    let test_data = vec![1, 2, 3, 4, 5];
    
    // Create mock AccountInfo
    let mock_account = MockAccountInfo::new(test_data.clone());
    
    // Call borrow_data_unchecked (requires unsafe block)
    let borrowed_data = unsafe { mock_account.borrow_data_unchecked() };
    
    // Print results
    // println!("Borrowed data: {:?}", borrowed_data);
    // println!("Data length: {}", borrowed_data.len());
    
    // Verify data is correct
    // assert_eq!(borrowed_data, &[1, 2, 3, 4, 5]);
    // println!("Verification passed!");
}