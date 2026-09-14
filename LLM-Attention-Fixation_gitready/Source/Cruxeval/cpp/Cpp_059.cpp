#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::vector<char> a;
    for(char c : s) {
        if(c != ' ') {
            a.push_back(c);
        }
    }

    std::vector<char> b = a;
    for(auto it = a.rbegin(); it != a.rend(); ++it) {
        if(*it == ' ') {
            b.pop_back();
        } else {
            break;
        }
    }

    return std::string(b.begin(), b.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("hi ")) == ("hi"));
}
