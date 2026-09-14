#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::vector<std::string> array, long value) {
    std::reverse(array.begin(), array.end());
    array.pop_back();
    std::vector<std::map<std::string, long>> odd;
    while (!array.empty()) {
        std::map<std::string, long> tmp;
        tmp[array.back()] = value;
        odd.push_back(tmp);
        array.pop_back();
    }
    std::map<std::string, long> result;
    while (!odd.empty()) {
        for (auto& elem : odd.back()) {
            result[elem.first] = elem.second;
        }
        odd.pop_back();
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"23"})), (123)) == (std::map<std::string,long>()));
}
