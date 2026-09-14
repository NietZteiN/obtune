#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    long m = *std::max_element(nums.begin(), nums.end());
    for (int i = 0; i < m; i++) {
        std::reverse(nums.begin(), nums.end());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)43, (long)0, (long)4, (long)77, (long)5, (long)2, (long)0, (long)9, (long)77}))) == (std::vector<long>({(long)77, (long)9, (long)0, (long)2, (long)5, (long)77, (long)4, (long)0, (long)43})));
}
