#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string alphabet, std::string s) {
    std::vector<std::string> a;
    for (char c : alphabet) {
        if (std::toupper(c) != c && s.find(std::toupper(c)) != std::string::npos) {
            a.push_back(std::string(1, c));
        }
    }
    if (std::all_of(s.begin(), s.end(), ::isupper)) {
        a.push_back("all_uppercased");
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("abcdefghijklmnopqrstuvwxyz"), ("uppercased # % ^ @ ! vz.")) == (std::vector<std::string>()));
}
