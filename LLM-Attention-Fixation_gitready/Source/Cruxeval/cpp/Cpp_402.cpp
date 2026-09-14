#include<assert.h>
#include<bits/stdc++.h>
std::map<long,long> f(long n, std::vector<std::string> l) {
    std::map<long,long> archive;
    for (int i = 0; i < n; ++i) {
        archive.clear();
        for (const std::string& x : l) {
            archive[x.size() + 10] = x.size() * 10;
        }
    }
    return archive;
}
int main() {
    auto candidate = f;
    assert(candidate((0), (std::vector<std::string>({(std::string)"aaa", (std::string)"bbb"}))) == (std::map<long,long>()));
}
