#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    long a = -1;
    std::vector<long> b(nums.begin() + 1, nums.end());
    while (a <= b[0]) {
        nums.erase(std::remove(nums.begin(), nums.end(), b[0]), nums.end());
        a = 0;
        b.erase(b.begin());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)5, (long)3, (long)-2, (long)-6, (long)8, (long)8}))) == (std::vector<long>({(long)-1, (long)-2, (long)-6, (long)8, (long)8})));
}
