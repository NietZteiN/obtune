#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> nums;
    for (char& c : text) {
        if (std::isdigit(c)) {
            nums.push_back(c);
        }
    }
    assert(nums.size() > 0);
    return std::string(nums.begin(), nums.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("-123   	+314")) == ("123314"));
}
