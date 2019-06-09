%textFileName = "top50tracks.txt";
textFileName = "logitech's_Lean.txt";
size = 1743;
initialDataArray = getTextFromFile(textFileName);
finalDataArray = modifyDataArray(initialDataArray);

%cellwrite("spotipyoutput.csv", finalDataArray);

trackNamesData = finalDataArray(:, 1);
acousticnessData = finalDataArray(:, 2);
danceabilityData = finalDataArray(:, 3);
durationData = finalDataArray(:, 4);
energyData = finalDataArray(:, 5);
instrumentalnessData = finalDataArray(:, 6);
keyData = finalDataArray(:, 7);
livenessData = finalDataArray(:, 8);
loudnessData = finalDataArray(:, 9);
modeData = finalDataArray(:, 10);
speechinessData = finalDataArray(:, 11);
tempoData = finalDataArray(:, 12);
timeSignatureData = finalDataArray(:, 13);
valenceData = finalDataArray(:, 14);

%trackNamesData = convertCell(trackNamesData);
acousticnessData = convertCell(acousticnessData);
danceabilityData = convertCell(danceabilityData);
durationData = convertCell(durationData);
energyData = convertCell(energyData);
instrumentalnessData = convertCell(instrumentalnessData);
keyData = convertCell(keyData);
livenessData = convertCell(livenessData);
loudnessData = convertCell(loudnessData);
modeData = convertCell(modeData);
speechinessData = convertCell(speechinessData);
tempoData = convertCell(tempoData);
timeSignatureData = convertCell(timeSignatureData);
valenceData = convertCell(valenceData);

%These are all the graphs that are created and are used to come to
%conclusions regarding the variables drawn from the Spotipy API.


% Is there a pattern to why I like some songs more than others?
scatter(1:size, instrumentalnessData, 'blue', 'filled')
hold on
scatter(1:size, livenessData, 'red', 'filled')
hold on
scatter(1:size, speechinessData, 'green', 'filled')
legend('Instrumentalness','Liveness', 'Speechiness')
title('Spotipy API')
xlabel('Rank of Songs (1 to 50)')
ylabel('Value (0.0 to 1.0)')

set(gcf,'position', [20,20,1300,700])

close all

scatter(tempoData, energyData, 'blue', 'filled')
title('Tempo v. Energy')
xlabel('Tempo (bpm)')
ylabel('Energy (0.0 to 1.0)')

close all

scatter(1:size, valenceData, 'blue', 'filled')
hold on
scatter(1:size, (energyData.^2 + danceabilityData.^2)-0.5, 'red', 'filled')
title('Valence & Danceability+Energy')
xlabel('Rank of Song (1 to 50)')
ylabel('Value')


close all

scatter(tempoData, danceabilityData, 'blue', 'filled')
title('Tempo v. Danceability')
xlabel('Tempo (bpm)')
ylabel('Danceability (0.0 to 1.0)')

close all

histogram(acousticnessData, 10)
title('Histogram of Acousticness')
xlabel('Acousticness (0 to 1)')
ylabel('Frequency #')

close all

histogram2(energyData, danceabilityData)
xlabel('Energy (0 to 1)')
ylabel('Danceability (0 to 1)')
title('Histogram of Energy & Danceability')


close all



h = scatter(danceabilityData,energyData, 'filled'); %// initiallize plot. Get a handle to graphic object
axis([0 1 0 1]); %// freeze axes
title('Danceability & Energy Distribution')
xlabel('Danceability')
ylabel('Energy')
for ii = 1:size
    %pause(0.001)
    set(h, 'XData', danceabilityData(1:ii), 'YData', energyData(1:ii));
    %drawnow %// you can probably remove this line, as pause already calls drawnow
end

close all

%scatter(1:size,(valenceData), 10, 'filled')

%plot(1:size, (valenceData(1:size)).^1);
%slope = valenceData(1:size)/(1:size);

err = immse(danceabilityData, energyData);
scatter(energyData, danceabilityData)
xlabel('Energy (0 to 1)')
ylabel('Danceability (0 to 1)')
title('Scatterplot of Energy & Danceability')
disp(err)
















