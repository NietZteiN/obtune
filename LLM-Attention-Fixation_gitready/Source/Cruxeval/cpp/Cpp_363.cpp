#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    std::sort(nums.begin(), nums.end());
    int n = nums.size();
    std::vector<long> new_nums;
    
    new_nums.push_back(nums[n/2]);
    
    if (n % 2 == 0) {
        new_nums.push_back(nums[n/2 - 1]);
    }
    
    for (int i = 0; i < n/2; i++) {
        new_nums.insert(new_nums.begin(), nums[n-i-1]);
        new_nums.push_back(nums[i]);
    }
    
    return new_nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1}))) == (std::vector<long>({(long)1})));
}
