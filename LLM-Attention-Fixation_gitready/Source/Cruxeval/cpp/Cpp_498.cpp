#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long idx, long added) {
    nums.insert(nums.begin() + idx, added);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)2, (long)2, (long)3, (long)3})), (2), (3)) == (std::vector<long>({(long)2, (long)2, (long)3, (long)2, (long)3, (long)3})));
}
