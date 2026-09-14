#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string value) {
    std::vector<char> ls(value.begin(), value.end());
    ls.push_back('N');
    ls.push_back('H');
    ls.push_back('I');
    ls.push_back('B');
    return std::string(ls.begin(), ls.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("ruam")) == ("ruamNHIB"));
}
