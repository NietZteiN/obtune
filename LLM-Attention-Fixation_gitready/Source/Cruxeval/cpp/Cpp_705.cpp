#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> cities, std::string name) {
    if (name.empty()) {
        return cities;
    } else if (!name.empty() && name != "cities") {
        return std::vector<std::string>();
    } else {
        std::vector<std::string> result;
        for (const auto& city : cities) {
            result.push_back(name + city);
        }
        return result;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"Sydney", (std::string)"Hong Kong", (std::string)"Melbourne", (std::string)"Sao Paolo", (std::string)"Istanbul", (std::string)"Boston"})), ("Somewhere ")) == (std::vector<std::string>()));
}
