#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::vector<std::string> strings) {
    std::map<std::string, long> occurrences;
    for (const std::string& str : strings) {
        if (occurrences.find(str) == occurrences.end()) {
            occurrences[str] = std::count(strings.begin(), strings.end(), str);
        }
    }
    return occurrences;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"La", (std::string)"Q", (std::string)"9", (std::string)"La", (std::string)"La"}))) == (std::map<std::string,long>({{"La", 3}, {"Q", 1}, {"9", 1}})));
}
