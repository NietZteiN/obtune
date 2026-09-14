#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    for (int i = 0; i < count / 2; i++) {
        std::swap(nums[i], nums[count - i - 1]);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)6, (long)1, (long)3, (long)1}))) == (std::vector<long>({(long)1, (long)3, (long)1, (long)6, (long)2})));
}
