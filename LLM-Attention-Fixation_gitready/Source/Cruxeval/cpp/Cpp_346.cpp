#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string filename) {
    std::string suffix = filename.substr(filename.find_last_of('.') + 1);
    std::string f2 = filename + std::string(suffix.rbegin(), suffix.rend());
    return f2.substr(f2.size() - suffix.size()) == suffix;
}
int main() {
    auto candidate = f;
    assert(candidate(("docs.doc")) == (false));
}
