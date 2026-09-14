#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    for (int i = 0; i < count; i++) {
        nums.insert(nums.begin() + i, nums[i]*2);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)8, (long)-2, (long)9, (long)3, (long)3}))) == (std::vector<long>({(long)4, (long)4, (long)4, (long)4, (long)4, (long)4, (long)2, (long)8, (long)-2, (long)9, (long)3, (long)3})));
}
