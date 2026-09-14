#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<std::string> names, std::vector<std::string> winners) {
    std::vector<long> result;
    for (const auto& name : names) {
        auto it = std::find(winners.begin(), winners.end(), name);
        if (it != winners.end()) {
            result.push_back(std::distance(names.begin(), it));
        }
    }
    
    std::sort(result.rbegin(), result.rend());
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"e", (std::string)"f", (std::string)"j", (std::string)"x", (std::string)"r", (std::string)"k"})), (std::vector<std::string>({(std::string)"a", (std::string)"v", (std::string)"2", (std::string)"im", (std::string)"nb", (std::string)"vj", (std::string)"z"}))) == (std::vector<long>()));
}
