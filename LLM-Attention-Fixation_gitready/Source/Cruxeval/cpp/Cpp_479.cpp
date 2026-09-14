#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long pop1, long pop2) {
    nums.erase(nums.begin() + pop1 - 1);
    nums.erase(nums.begin() + pop2 - 1);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)5, (long)2, (long)3, (long)6})), (2), (4)) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
