#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string r, std::string w) {
    std::vector<std::string> a;
    if (r[0] == w[0] && w[w.size()-1] == r[r.size()-1]) {
        a.push_back(r);
        a.push_back(w);
    } else {
        a.push_back(w);
        a.push_back(r);
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("ab"), ("xy")) == (std::vector<std::string>({(std::string)"xy", (std::string)"ab"})));
}
