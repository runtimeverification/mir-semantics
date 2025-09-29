#[repr(C)]
#[derive(Clone, Copy, Default)]
pub(crate) struct Account {
    /// Length of the data. Modifiable by programs.
    pub(crate) data_len: u64,
}

#[repr(C)]
#[derive(Clone, PartialEq, Eq, Debug)]
pub struct AccountInfo {
    /// Raw (pointer to) account data.
    ///
    /// Note that this is a pointer can be shared across multiple `AccountInfo`.
    pub(crate) raw: *mut Account,
}

impl AccountInfo {
    #[inline(always)]
    pub unsafe fn borrow_data_unchecked(&self) -> &[u8] {
        core::slice::from_raw_parts(self.data_ptr(), self.data_len())
    }

    /// Returns the memory address of the account data.
    fn data_ptr(&self) -> *mut u8 {
        unsafe { (self.raw as *const _ as *mut u8).add(core::mem::size_of::<Account>()) }
    }

    /// Returns the size of the data in the account.
    #[inline(always)]
    pub fn data_len(&self) -> usize {
        unsafe { (*self.raw).data_len as usize }
    }
}

// Test function for deref functionality
fn test_deref(account: &AccountInfo) {
    unsafe {
        assert_eq!(account.borrow_data_unchecked(), &[0; 100]);
    }
}

fn main() {
    // Create test data with actual data storage
    let account_data1 = vec![0u8; 100];
    let account_data2 = vec![0u8; 200];
    let account_data3 = vec![0u8; 300];
    
    // Create accounts with data
    let account1 = Account { data_len: 100 };
    let account2 = Account { data_len: 200 };
    let account3 = Account { data_len: 300 };
    
    // Create a combined structure: Account + data
    let mut combined1 = vec![];
    combined1.extend_from_slice(&account1.data_len.to_ne_bytes());
    combined1.extend_from_slice(&account_data1);
    
    let mut combined2 = vec![];
    combined2.extend_from_slice(&account2.data_len.to_ne_bytes());
    combined2.extend_from_slice(&account_data2);
    
    let mut combined3 = vec![];
    combined3.extend_from_slice(&account3.data_len.to_ne_bytes());
    combined3.extend_from_slice(&account_data3);
    
    // Create AccountInfo with pointers to the combined data
    let accounts = [
        AccountInfo { raw: combined1.as_mut_ptr() as *mut Account },
        AccountInfo { raw: combined2.as_mut_ptr() as *mut Account },
        AccountInfo { raw: combined3.as_mut_ptr() as *mut Account },
    ];

    test_deref(&accounts[0]);
}