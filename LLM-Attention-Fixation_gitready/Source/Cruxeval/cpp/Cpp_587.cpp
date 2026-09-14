#include<assert.h>
#include<bits/stdc++.h>
std::map<long,std::string> f(std::vector<long> nums, std::string fill) {
    std::map<long,std::string> ans;
    for (long n : nums) {
        ans[n] = fill;
    }
    return ans;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)1, (long)1, (long)2})), ("abcca")) == (std::map<long,std::string>({{0, "abcca"}, {1, "abcca"}, {2, "abcca"}})));
}
