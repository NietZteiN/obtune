#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long target) {
    if (std::count(nums.begin(), nums.end(), 0)) {
        return 0;
    } else if (std::count(nums.begin(), nums.end(), target) < 3) {
        return 1;
    } else {
        return std::find(nums.begin(), nums.end(), target) - nums.begin();
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)1, (long)2})), (3)) == (1));
}
