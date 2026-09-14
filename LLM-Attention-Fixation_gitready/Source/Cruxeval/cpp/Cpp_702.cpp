#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    for (int i = count - 1; i >= 0; --i) {
        long value = nums[0];
        nums.erase(nums.begin());
        nums.insert(nums.begin() + i, value);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)-5, (long)-4}))) == (std::vector<long>({(long)-4, (long)-5, (long)0})));
}
