#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long target) {
    int cnt = std::count(nums.begin(), nums.end(), target);
    return cnt * 2;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1})), (1)) == (4));
}
