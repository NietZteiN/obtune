#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string str) {
    std::string tmp = str;
    for (char& c : tmp) {
        c = std::tolower(c);
    }
    for (char& c : str) {
        c = std::tolower(c);
        size_t pos = tmp.find(c);
        if (pos != std::string::npos) {
            tmp.erase(pos, 1);
        }
    }
    return tmp;
}
int main() {
    auto candidate = f;
    assert(candidate(("[ Hello ]+ Hello, World!!_ Hi")) == (""));
}
