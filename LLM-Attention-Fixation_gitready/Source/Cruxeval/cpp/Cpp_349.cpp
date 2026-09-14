#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::map<std::string,long> dictionary) {
    dictionary["1049"] = 55;
    auto last_item = *dictionary.rbegin();
    dictionary.erase(last_item.first);
    dictionary[last_item.first] = last_item.second;
    return dictionary;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"noeohqhk", 623}}))) == (std::map<std::string,long>({{"noeohqhk", 623}, {"1049", 55}})));
}
