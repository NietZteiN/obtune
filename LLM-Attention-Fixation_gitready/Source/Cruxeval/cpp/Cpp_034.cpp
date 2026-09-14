#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long odd1, long odd2) {
    while (std::find(nums.begin(), nums.end(), odd1) != nums.end()) {
        nums.erase(std::remove(nums.begin(), nums.end(), odd1), nums.end());
    }
    while (std::find(nums.begin(), nums.end(), odd2) != nums.end()) {
        nums.erase(std::remove(nums.begin(), nums.end(), odd2), nums.end());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)7, (long)7, (long)6, (long)8, (long)4, (long)1, (long)2, (long)3, (long)5, (long)1, (long)3, (long)21, (long)1, (long)3})), (3), (1)) == (std::vector<long>({(long)2, (long)7, (long)7, (long)6, (long)8, (long)4, (long)2, (long)5, (long)21})));
}
