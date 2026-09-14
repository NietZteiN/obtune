#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long spot, long idx) {
    nums.insert(nums.begin() + spot, idx);
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)0, (long)1, (long)1})), (0), (9)) == (std::vector<long>({(long)9, (long)1, (long)0, (long)1, (long)1})));
}
