#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string c1, std::string c2) {
    if (s == "") {
        return s;
    }
    std::vector<std::string> ls;
    std::istringstream iss(s);
    std::string item;
    while (std::getline(iss, item, c1[0])) {
        if (item.find(c1) != std::string::npos) {
            item.replace(item.find(c1), c1.length(), c2);
        }
        ls.push_back(item);
    }
    return c1 + std::accumulate(std::next(ls.begin()), ls.end(), ls[0], [&](const std::string &a, const std::string &b) {
        return a + c1 + b;
    });
}
int main() {
    auto candidate = f;
    assert(candidate((""), ("mi"), ("siast")) == (""));
}
