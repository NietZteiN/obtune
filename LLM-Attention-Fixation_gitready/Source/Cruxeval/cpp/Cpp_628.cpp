#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long delete_element) {
    nums.erase(std::remove(nums.begin(), nums.end(), delete_element), nums.end());
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)5, (long)3, (long)6, (long)1})), (5)) == (std::vector<long>({(long)4, (long)3, (long)6, (long)1})));
}
