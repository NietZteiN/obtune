#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> fruits) {
    if(fruits.back() == fruits.front()) {
        std::vector<std::string> result;
        result.push_back("no");
        return result;
    } else {
        fruits.erase(fruits.begin());
        fruits.pop_back();
        fruits.erase(fruits.begin());
        fruits.pop_back();
        return fruits;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"apple", (std::string)"apple", (std::string)"pear", (std::string)"banana", (std::string)"pear", (std::string)"orange", (std::string)"orange"}))) == (std::vector<std::string>({(std::string)"pear", (std::string)"banana", (std::string)"pear"})));
}
