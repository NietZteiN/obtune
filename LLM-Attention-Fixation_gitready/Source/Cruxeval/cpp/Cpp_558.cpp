#include<assert.h>
#include<bits/stdc++.h>
bool f(std::vector<long> nums, std::vector<long> mos) {
    for (int num : mos) {
        nums.erase(std::remove(nums.begin(), nums.end(), num), nums.end());
    }
    std::sort(nums.begin(), nums.end());
    for (int num : mos) {
        nums.push_back(num);
    }
    for (int i = 0; i < nums.size() - 1; i++) {
        if (nums[i] > nums[i+1]) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)1, (long)2, (long)1, (long)4, (long)1})), (std::vector<long>({(long)1}))) == (false));
}
