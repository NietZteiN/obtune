#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    std::vector<long> asc = nums;
    std::vector<long> desc;
    std::reverse(asc.begin(), asc.end());
    desc = std::vector<long>(asc.begin(), asc.begin() + asc.size()/2);
    desc.insert(desc.end(), asc.begin(), asc.end());
    desc.insert(desc.end(), desc.begin(), desc.end());
    return desc;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
