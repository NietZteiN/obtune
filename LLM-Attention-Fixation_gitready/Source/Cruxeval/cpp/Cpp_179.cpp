#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    std::vector<long> nums_copy = nums;
    int count = nums_copy.size();
    for (int i = -count+1; i < 0; i++) {
        nums_copy.insert(nums_copy.begin(), nums_copy[nums_copy.size() + i]);
    }
    return nums_copy;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)7, (long)1, (long)2, (long)6, (long)0, (long)2}))) == (std::vector<long>({(long)2, (long)0, (long)6, (long)2, (long)1, (long)7, (long)1, (long)2, (long)6, (long)0, (long)2})));
}
