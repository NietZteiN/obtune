#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> d, std::vector<std::string> l) {
    std::map<std::string, long> new_d;

    for (const std::string& k : l) {
        if (d.find(k) != d.end()) {
            new_d[k] = d[k];
        }
    }

    return new_d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"lorem ipsum", 12}, {"dolor", 23}})), (std::vector<std::string>({(std::string)"lorem ipsum", (std::string)"dolor"}))) == (std::map<std::string,long>({{"lorem ipsum", 12}, {"dolor", 23}})));
}
