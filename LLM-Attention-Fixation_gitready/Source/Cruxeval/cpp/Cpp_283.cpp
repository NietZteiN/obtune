#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::map<std::string,long> dictionary, std::string key) {
    dictionary.erase(key);
    if (std::min_element(dictionary.begin(), dictionary.end())->first == key) {
        key = dictionary.begin()->first;
    }
    return key;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"Iron Man", 4}, {"Captain America", 3}, {"Black Panther", 0}, {"Thor", 1}, {"Ant-Man", 6}})), ("Iron Man")) == ("Iron Man"));
}
