#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text, std::string sep) {
    std::vector<std::string> result;
    size_t pos = 0;
    size_t found;
    int maxsplit = 2;
    
    while ((found = text.find(sep, pos)) != std::string::npos && maxsplit > 0) {
        result.push_back(text.substr(pos, found - pos));
        pos = found + sep.length();
        maxsplit--;
    }
    
    result.push_back(text.substr(pos));

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("a-.-.b"), ("-.")) == (std::vector<std::string>({(std::string)"a", (std::string)"", (std::string)"b"})));
}
