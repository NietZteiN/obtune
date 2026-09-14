#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long pos, long value) {
    nums.insert(nums.begin() + pos, value);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)1, (long)2})), (2), (0)) == (std::vector<long>({(long)3, (long)1, (long)0, (long)2})));
}
