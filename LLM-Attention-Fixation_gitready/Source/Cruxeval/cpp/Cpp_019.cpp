#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string x, std::string y) {
    std::reverse(y.begin(), y.end());
    for (auto &c : y) {
        if (c == '9') c = '0';
        else if (c == '0') c = '9';
    }
    if (x.find_first_not_of("0123456789") == std::string::npos && y.find_first_not_of("0123456789") == std::string::npos)
        return x + y;
    else 
        return x;
}
int main() {
    auto candidate = f;
    assert(candidate((""), ("sdasdnakjsda80")) == (""));
}
