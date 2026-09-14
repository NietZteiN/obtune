#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::vector<std::string>> f(std::map<std::string,std::vector<std::string>> playlist, std::string liker_name, std::string song_index) {
    playlist[liker_name].push_back(song_index);
    return playlist;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::vector<std::string>>({{"aki", std::vector<std::string>({(std::string)"1", (std::string)"5"})}})), ("aki"), ("2")) == (std::map<std::string,std::vector<std::string>>({{"aki", std::vector<std::string>({(std::string)"1", (std::string)"5", (std::string)"2"})}})));
}
