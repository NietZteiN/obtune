#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::vector<std::string> values, long value) {
    std::map<std::string, long> new_dict;
    int length = values.size();
    for (const std::string& val : values) {
        new_dict[val] = value;
    }
    std::sort(values.begin(), values.end());
    new_dict[std::accumulate(values.begin(), values.end(), std::string(""))] = value * 3;
    return new_dict;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"0", (std::string)"3"})), (117)) == (std::map<std::string,long>({{"0", 117}, {"3", 117}, {"03", 351}})));
}
