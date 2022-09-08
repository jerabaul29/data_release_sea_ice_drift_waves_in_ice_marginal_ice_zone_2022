readTrusted <- function(filename=NA, folder='C:/Users/a5406/Documents/Telletokt2022/Trusted',
                        deployed=c('T1', 'T2', 'T3', 'T4', 'T5'), 
                        deploy.time=c('2022-03-21 17:48:00', '2022-03-21 16:37:00', 
                                      '2022-03-22 10:25:00', '2022-03-22 15:26:00',
                                      '2022-03-22 18:05:00')) {
  require(rgdal)
  if(!is.na(filename)) {
    trust <- readLines(filename)
  } else {
    allFiles <- dir(folder)
    allFiles <- allFiles[grep('AdvancedExport', allFiles)]
    saveDates <- gsub('AdvancedExport_', '', allFiles)
    saveDates <- gsub('Z.csv', '', saveDates)
    saveDates <- gsub('_', ':', saveDates)
    saveDates <- as.POSIXct(saveDates, tz='UTC')
    saveLatest <- which.max(saveDates)
    trust <- readLines(paste(folder, allFiles[saveLatest], sep='/'))
  }  
  trustNames <- trust[1]
  trustnames <- gsub(' Brussels, Copenhagen, Madrid, Paris', '', trustNames)
  trustNames <- unlist(strsplit(trustNames, ','))
  trustNames <- gsub("Unit ActivationDate ((UTC+01:00) Brussels", "Unit ActivationDate (UTC+01:00)", trustNames, fixed=T)
  trustNames <- gsub("Timestamp ((UTC+01:00) Brussels", "Timestamp (UTC+01:00)", trustNames, fixed=T)
  trustNames <- gsub("PeakAccelerationTime ((UTC+01:00) Brussels", "PeakAccelerationTime (UTC+01:00)", trustNames, fixed=T)
  trustNames <- setdiff(trustNames, c(" Copenhagen", " Madrid", " Paris)"))
  
  trust <- trust[-1]
  
  trustList <- list()
  for(i in 1:length(trust)) {
    tmp <- unlist(strsplit(trust[i], ','))
    tmp[10] <- paste(tmp[10], tmp[11], sep='.')
    tmp[12] <- paste(tmp[12], tmp[13], sep='.')
    trustList[[i]] <- tmp[c(1,2,c(7,8,9,10,12,14))]
  }
  
  trustDF <- data.frame(do.call('rbind', trustList))
  
  names(trustDF) <- trustNames[c(1,2,7,8,9,10,11,12)]
  
  names(trustDF)[c(1, 3, 4, 8)] <- c('SerialNumber', 'UTC', 'CET', 'Accuracy')
  

  trustDF$SerialNumber <- gsub('="', '', trustDF$SerialNumber)
  trustDF$UnitName <- gsub('="', '', trustDF$UnitName)
  trustDF$PositionType <- gsub('="', '', trustDF$PositionType)
  trustDF$SerialNumber <- gsub('"', '', trustDF$SerialNumber)
  trustDF$UnitName <- gsub('"', '', trustDF$UnitName)
  trustDF$PositionType <- gsub('"', '', trustDF$PositionType)
  
  trustDF$UTC <-as.POSIXct(trustDF$UTC, tz='UTC')
  trustDF$CET <-as.POSIXct(trustDF$CET, tz='UTC')
  trustDF$Latitude <-as.numeric(trustDF$Latitude)
  trustDF$Longitude <-as.numeric(trustDF$Longitude)
  trustDF$Accuracy <-as.numeric(trustDF$Accuracy)
  trustDF <- trustDF[which(!is.na(trustDF$Longitude) & !is.na(trustDF$Latitude)),]
  trustDF <- trustDF[order(trustDF$UnitName, trustDF$UTC),]
  trustDF$Seq <- rep(NA, nrow(trustDF))
  for(i in unique(trustDF$UnitName)) {
    which.unit <- which(trustDF$UnitName==i)
    trustDF$Seq[which.unit] <- c(1:length(which.unit))
  }
  
  if(all(!is.na(deployed))) {
    trustDF <- trustDF[which(trustDF$UnitName %in% deployed),]
    keep <- rep(F, nrow(trustDF))
    deploy.time <- as.POSIXct(deploy.time, tz='UTC')
    for(i in 1:length(deployed)) {
      keep[which(trustDF$UnitName==deployed[i] & trustDF$UTC>=deploy.time[i])] <- T
    }
    trustDF <- trustDF[which(keep),]
  }  
  latest <- c((match(unique(trustDF$UnitName), trustDF$UnitName)[-1])-1, nrow(trustDF))
  latest <- trustDF[latest,]
  write.csv(latest, './Trusted/latest.csv', row.names=F)
  
  coordinates(trustDF) <- c('Longitude', 'Latitude')
  proj4string(trustDF) <- CRS('+proj=longlat +datum=WGS84 +no_defs')
  trustDF$speed <- trustDF$dist <- rep(NA, nrow(trustDF))
  for(i in 1:length(deployed)) {
    trustDF$dist[which(trustDF$UnitName==deployed[i])] <- c(NA, spDists(trustDF[which(trustDF$UnitName==deployed[i]),], segments=T, longlat=T))
    trustDF$speed[which(trustDF$UnitName==deployed[i])] <- 3600*c(NA, trustDF$dist[which(trustDF$UnitName==deployed[i])][-1]/diff(as.numeric(trustDF$UTC[which(trustDF$UnitName==deployed[i])])))
  }
   
  writeOGR(trustDF, './Trusted/trusted.shp', layer='UnitName', driver='ESRI Shapefile')
  writeOGR(trustDF, './Trusted/trusted.geojson', 
           layer='UnitName', driver='GeoJSON', overwrite_layer=T)
  
}
