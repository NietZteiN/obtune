#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    for (int num = 2; num < count; num++) {
        std::sort(nums.begin(), nums.end());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-6, (long)-5, (long)-7, (long)-8, (long)2}))) == (std::vector<long>({(long)-8, (long)-7, (long)-6, (long)-5, (long)2})));
}
