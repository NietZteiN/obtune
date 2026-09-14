#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result;
    for (char c : text) {
        if (std::isdigit(c)) {
            result.push_back(c);
        }
    }
    std::reverse(result.begin(), result.end());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("--4yrw 251-//4 6p")) == ("641524"));
}
