function [dataArray] = getTextFromFile(textFileName)

fileID = fopen(textFileName, 'r');
dataArray = textscan(fileID, '%s', 25000 , 'Delimiter', '\n');
dataArray = dataArray{1};

end

