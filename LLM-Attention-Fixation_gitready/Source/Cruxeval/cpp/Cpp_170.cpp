#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long number) {
    return std::count(nums.begin(), nums.end(), number);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)12, (long)0, (long)13, (long)4, (long)12})), (12)) == (2));
}
