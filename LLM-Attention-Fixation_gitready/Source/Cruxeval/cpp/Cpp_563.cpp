#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text1, std::string text2) {
    std::vector<int> nums;
    for(int i = 0; i < text2.length(); i++) {
        nums.push_back(std::count(text1.begin(), text1.end(), text2[i]));
    }
    return std::accumulate(nums.begin(), nums.end(), 0);
}
int main() {
    auto candidate = f;
    assert(candidate(("jivespdcxc"), ("sx")) == (2));
}
