#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    nums.clear();
    std::vector<long> result;
    for (long num : nums) {
        result.push_back(num * 2);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)3, (long)2, (long)1, (long)2, (long)-1, (long)4, (long)2}))) == (std::vector<long>()));
}
