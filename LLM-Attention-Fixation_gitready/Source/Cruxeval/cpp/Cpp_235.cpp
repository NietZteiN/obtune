#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> array, std::vector<std::string> arr) {
    std::vector<std::string> result;
    for (std::string s : arr) {
        std::string delimiter = arr[std::distance(array.begin(), std::find(array.begin(), array.end(), s))];
        std::istringstream ss(s);
        std::string token;
        while (std::getline(ss, token, delimiter.c_str()[0])) {
            if (token != "") {
                result.push_back(token);
            }
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>()), (std::vector<std::string>())) == (std::vector<std::string>()));
}
