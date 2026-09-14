#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> seq, std::string v) {
    std::vector<std::string> a;
    for (const std::string& i : seq) {
        if (i.size() >= v.size() && i.substr(i.size() - v.size()) == v) {
            a.push_back(i + i);
        }
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"oH", (std::string)"ee", (std::string)"mb", (std::string)"deft", (std::string)"n", (std::string)"zz", (std::string)"f", (std::string)"abA"})), ("zz")) == (std::vector<std::string>({(std::string)"zzzz"})));
}
