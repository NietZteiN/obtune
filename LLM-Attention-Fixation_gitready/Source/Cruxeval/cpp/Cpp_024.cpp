#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long i) {
    nums.erase(nums.begin() + i);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)35, (long)45, (long)3, (long)61, (long)39, (long)27, (long)47})), (0)) == (std::vector<long>({(long)45, (long)3, (long)61, (long)39, (long)27, (long)47})));
}
