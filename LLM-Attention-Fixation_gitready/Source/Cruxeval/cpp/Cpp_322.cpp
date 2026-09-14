#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> chemicals, long num) {
    std::vector<std::string> fish(chemicals.begin() + 1, chemicals.end());
    std::reverse(chemicals.begin(), chemicals.end());
    for (long i = 0; i < num; i++) {
        fish.push_back(chemicals[1]);
        chemicals.erase(chemicals.begin() + 1);
    }
    std::reverse(chemicals.begin(), chemicals.end());
    return chemicals;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"lsi", (std::string)"s", (std::string)"t", (std::string)"t", (std::string)"d"})), (0)) == (std::vector<std::string>({(std::string)"lsi", (std::string)"s", (std::string)"t", (std::string)"t", (std::string)"d"})));
}
