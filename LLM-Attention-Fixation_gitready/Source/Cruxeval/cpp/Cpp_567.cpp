#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string s, long n) {
    std::vector<std::string> ls;
    std::stringstream ss(s);
    std::string temp;
    while (ss >> temp)
        ls.push_back(temp);
    std::vector<std::string> out;
    while (ls.size() >= n) {
        for (auto it = ls.end() - n; it != ls.end(); ++it)
            out.push_back(*it);
        ls.erase(ls.end() - n, ls.end());
    }
    std::string join_str = "_";
    if (!out.empty()) {
        for (auto it = out.begin() + 1; it != out.end(); ++it)
            out[0] += join_str + *it;
    }
    ls.push_back(out[0]);
    return ls;
}
int main() {
    auto candidate = f;
    assert(candidate(("one two three four five"), (3)) == (std::vector<std::string>({(std::string)"one", (std::string)"two", (std::string)"three_four_five"})));
}
