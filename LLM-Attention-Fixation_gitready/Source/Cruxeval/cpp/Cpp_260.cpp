#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long start, long k) {
    std::reverse(nums.begin() + start, nums.begin() + start + k);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)5, (long)6})), (4), (2)) == (std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)6, (long)5})));
}
